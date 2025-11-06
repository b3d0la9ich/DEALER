# ===== build =====
FROM golang:1.23-alpine AS build
WORKDIR /src

# зависимости
COPY go.mod ./
# если есть go.sum — тоже скопируй
# COPY go.sum ./
RUN go mod download

# код
COPY . .
RUN go mod tidy

# <<< ВАЖНО: создать каталог /out!
RUN mkdir -p /out && CGO_ENABLED=0 go build -o /out/inquiries ./main.go

# ===== runtime =====
FROM alpine:3.20
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=build /out/inquiries /app/inquiries
ENV PORT=8080
EXPOSE 8080
CMD ["/app/inquiries"]
