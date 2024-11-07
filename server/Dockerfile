FROM node:alpine
WORKDIR /app

# Add files
COPY index.html .
COPY server.js .

# Install dependencies
RUN npm install minio express env-var

# Define the command to run your application
CMD ["npm", "start", "--", "--port", "8080"]