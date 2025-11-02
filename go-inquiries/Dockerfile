# ===== build =====
FROM golang:1.23-alpine AS build
WORKDIR /src

# 1) тянем зависимости по go.mod (go.sum может отсутствовать)
COPY go.mod .
RUN go mod download

# 2) копируем код и формируем go.sum
COPY . .
RUN go mod tidy

# 3) сборка статического бинарника
RUN CGO_ENABLED=0 go build -o /out/inquiries main.go

# ===== runtime =====
FROM alpine:3.20
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=build /out/inquiries /app/inquiries
ENV PORT=8080
EXPOSE 8080
CMD ["/app/inquiries"]
