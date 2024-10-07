import json
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

from loguru import logger
from minio import Minio
from sfapi_client import Client
from sfapi_client.compute import Machine


def mino_client():
    creds = json.loads((Path().home() / ".minio" / "credentials.json").read_text())
    fqdn, port = urlparse(creds["url"]).netloc.split(":")

    # Create a MinIO client
    client = Minio(
        fqdn,
        access_key=creds["accessKey"],
        secret_key=creds["secretKey"],
        secure=True,
        region="",
    )
    return client


def watch_for_data():
    client = mino_client()
    with client.listen_bucket_notification(
        "data",
        events=["s3:ObjectCreated:*", "s3:ObjectRemoved:*"],
    ) as events:
        for event in events:
            for ev in event["Records"]:
                if "s3:ObjectCreated" in ev["eventName"]:
                    yield ev


def status():
    with Client() as client:
        status = client.compute(Machine.perlmutter)
    logger.debug(status.status)


script = """#!/bin/bash
#SBATCH -A nstaff
#SBATCH -C cron
#SBATCH -q workflow
#SBATCH -N 1
#SBATCH -c 1
#SBATCH -t 2
#SBATCH --chdir={user_scratch}/mino_s3_demo
#SBATCH -o {user_scratch}/mino_s3_demo/sfapi_demo.out
#SBATCH -e {user_scratch}/mino_s3_demo/sfapi_demo.err

export PATH=$PATH:{user_home}/.local/bin

mc cp spin/{bucket}/{file_name} .

module load python
python plot_data.py {file_name}
"""


def start_job(bucket, file_name):
    key = Path().home() / ".superfacility" / "sfapi.pem"
    with Client(key=key) as client:
        user = client.user()
        user_scratch = (Path("/pscratch/sd") / user.name[0] / user.name).as_posix()
        user_home = (Path("/global/homes") / user.name[0] / user.name).as_posix()

        compute = client.compute(Machine.perlmutter)
        client._wait_interval = 2
        job = compute.submit_job(
            script.format(
                bucket=bucket,
                file_name=file_name,
                user_scratch=user_scratch,
                user_home=user_home,
            )
        )
        logger.info(f"Submitted {job.jobid} for {file_name}")
        job.complete()
        logger.info(f"{job.jobid} Completed")
        img_out = Path().cwd() / f"{file_name[:-4]}.png"
        [image] = compute.ls(f"{user_scratch}/mino_s3_demo/{file_name[:-4]}.png")
        logger.debug(f"Downloading {image}")
        img_out.write_bytes(image.download().read())
        logger.debug(f"Finished {file_name}")


def server():
    try:
        logger.info("Starting server and waiting for data")
        jobs = []
        for event in watch_for_data():
            bucket = event["s3"]["bucket"]["name"]
            obj = event["s3"]["object"]["key"]
            logger.debug(f"Data added to {bucket}/{obj}")
            jobs.append(
                Thread(
                    target=start_job,
                    args=[
                        bucket,
                        obj,
                    ],
                )
            )
            jobs[-1].start()
    except KeyboardInterrupt:
        logger.info("Stopping threads")
        [j.join() for j in jobs]
    logger.info("end")
