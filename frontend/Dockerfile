FROM node:18-alpine

WORKDIR /app

# 接收构建参数
ARG NEXT_PUBLIC_API_URL

# 设置环境变量供构建时使用
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
