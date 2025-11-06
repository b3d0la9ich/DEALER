package main

import (
	"database/sql"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

/* ---------- Модели ---------- */

type Inquiry struct {
	ID            uint       `json:"id" gorm:"primaryKey"`
	CarID         uint       `json:"car_id" binding:"required"`
	BuyerID       uint       `json:"buyer_id" binding:"required"`
	SellerID      uint       `json:"seller_id" binding:"required"`
	Message       string     `json:"message" binding:"required"`
	PreferredTime *time.Time `json:"preferred_time"`
	ContactPhone  string     `json:"contact_phone"`
	Status        string     `json:"status" gorm:"type:varchar(16);default:'new'"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at"`
}

type InquiryFull struct {
	ID            uint       `json:"id"`
	CarID         uint       `json:"car_id"`
	BuyerID       uint       `json:"buyer_id"`
	SellerID      uint       `json:"seller_id"`
	Message       string     `json:"message"`
	PreferredTime *time.Time `json:"preferred_time"`
	ContactPhone  string     `json:"contact_phone"`
	Status        string     `json:"status"`
	CreatedAt     time.Time  `json:"created_at"`
	UpdatedAt     time.Time  `json:"updated_at"`
	CarName       string `json:"car_name"`
	CarVIN        string `json:"car_vin"`
	BuyerName     string `json:"buyer_name"`
	SellerName    string `json:"seller_name"`
}

/* ---------- DTO ---------- */

type CreateInquiryDTO struct {
	CarID         uint       `json:"car_id" binding:"required"`
	BuyerID       uint       `json:"buyer_id" binding:"required"`
	SellerID      uint       `json:"seller_id" binding:"required"`
	Message       string     `json:"message" binding:"required"`
	PreferredTime *time.Time `json:"preferred_time"`
	ContactPhone  string     `json:"contact_phone"`
}

type UpdateStatusDTO struct {
	Status string `json:"status" binding:"required,oneof=new accepted declined closed"`
}

/* ---------- main ---------- */

func main() {
	dsn := os.Getenv("PG_DSN")
	apiKey := os.Getenv("API_KEY")
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	if dsn == "" || apiKey == "" {
		log.Fatal("env PG_DSN and API_KEY are required")
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal(err)
	}
	if err := db.AutoMigrate(&Inquiry{}); err != nil {
		log.Fatal(err)
	}
	sqlDB, _ := db.DB()

	r := gin.Default()

	// probes
	r.GET("/health", func(c *gin.Context) { c.JSON(http.StatusOK, gin.H{"status": "ok"}) })
	r.GET("/ready", func(c *gin.Context) {
		if err := ping(sqlDB); err != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{"status": "db_down"})
			return
		}
		c.JSON(http.StatusOK, gin.H{"status": "ready"})
	})

	// 🔧 ВОТ ЭТО БЫЛО ЗАКОММЕНТИРОВАНО — ЭТО И ЕСТЬ "api"
	api := r.Group("/api", func(c *gin.Context) {
		if c.GetHeader("X-Api-Key") != apiKey {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
			return
		}
	})

	// POST /api/inquiries — создать
	api.POST("/inquiries", func(c *gin.Context) {
		var dto CreateInquiryDTO
		if err := c.ShouldBindJSON(&dto); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		in := Inquiry{
			CarID:         dto.CarID,
			BuyerID:       dto.BuyerID,
			SellerID:      dto.SellerID,
			Message:       dto.Message,
			PreferredTime: dto.PreferredTime,
			ContactPhone:  dto.ContactPhone,
		}
		if err := db.Create(&in).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusCreated, in)
	})

	// GET /api/inquiries — список
	api.GET("/inquiries", func(c *gin.Context) {
		var list []InquiryFull
		q := db.Table("inquiries AS i").
			Select(`
				i.id, i.car_id, i.buyer_id, i.seller_id, i.message, i.preferred_time,
				i.contact_phone, i.status, i.created_at, i.updated_at,
				COALESCE(cars.brand,'') || ' ' || COALESCE(cars.model,'') AS car_name,
				COALESCE(cars.vin,'') AS car_vin,
				COALESCE(buyers.full_name,'') AS buyer_name,
				COALESCE(sellers.full_name,'') AS seller_name
			`).
			Joins("LEFT JOIN cars ON cars.id = i.car_id").
			Joins("LEFT JOIN users AS buyers ON buyers.id = i.buyer_id").
			Joins("LEFT JOIN users AS sellers ON sellers.id = i.seller_id").
			Order("i.created_at DESC")

		if b := c.Query("buyer_id"); b != "" {
			q = q.Where("i.buyer_id = ?", b)
		}
		if s := c.Query("seller_id"); s != "" {
			q = q.Where("i.seller_id = ?", s)
		}

		if err := q.Find(&list).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, list)
	})

	// PUT /api/inquiries/:id/status — обновить статус
	api.PUT("/inquiries/:id/status", func(c *gin.Context) {
		var dto UpdateStatusDTO
		if err := c.ShouldBindJSON(&dto); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		if err := db.Model(&Inquiry{}).
			Where("id = ?", c.Param("id")).
			Update("status", dto.Status).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.Status(http.StatusNoContent)
	})

	log.Fatal(r.Run("0.0.0.0:" + port))
}

/* ---------- helpers ---------- */

func ping(db *sql.DB) error {
	db.SetConnMaxLifetime(time.Minute)
	return db.Ping()
}
