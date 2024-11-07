// In order to use the MinIO JavaScript API to generate the pre-signed URL, begin by instantiating
// a `Minio.Client` object and pass in the values for your server.
// The example below uses values for play.min.io:9000

const Minio = require('minio')
const env = require('env-var');

const SERVER_PORT = env.get('PORT').default('8080').asPortNumber()
const ENDPOINT = env.get('ENDPOINT').required().asString();
const ACCESS_KEY = env.get('ACCESS_KEY').required().asString();
const SECRET_KEY = env.get('SECRET_KEY').required().asString();
const BUCKET_NAME = env.get('BUCKET_NAME').default("uploads").required().asString();


var client = new Minio.Client({
    endPoint: ENDPOINT,
    port: 443,
    useSSL: true,
    accessKey: ACCESS_KEY,
    secretKey: SECRET_KEY
})

// Instantiate an `express` server and expose an endpoint called `/presignedUrl` as a `GET` request that
// accepts a filename through a query parameter called `name`. For the implementation of this endpoint,
// invoke [`presignedPutObject`](https://min.io/docs/minio/linux/developers/javascript/API.html#presignedPutObjectt) 
// on the `Minio.Client` instance to generate a pre-signed URL, and return that URL in the response:

// express is a small HTTP server wrapper, but this works with any HTTP server
const server = require('express')()

server.get('/presignedUrl', (req, res) => {
    client.presignedPutObject(BUCKET_NAME, req.query.name, (err, url) => {
        if (err) throw err
        res.end(url)
    })
})

server.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
})

server.listen(SERVER_PORT)