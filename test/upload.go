package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
)

func main() {
	checkAndCreateAWSCredentials()
}

func checkAndCreateAWSCredentials() {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		fmt.Println("Error getting home directory:", err)
		return
	}

	credentialsPath := filepath.Join(homeDir, ".aws", "credentials")

	if _, err := os.Stat(credentialsPath); os.IsNotExist(err) {
		fmt.Println("AWS credentials file not found. Let's create one.")

		reader := bufio.NewReader(os.Stdin)

		fmt.Print("Enter AWS Access Key ID: ")
		awsAccessKeyID, _ := reader.ReadString('\n')
		awsAccessKeyID = strings.TrimSpace(awsAccessKeyID)

		fmt.Print("Enter AWS Secret Access Key: ")
		awsSecretAccessKey, _ := reader.ReadString('\n')
		awsSecretAccessKey = strings.TrimSpace(awsSecretAccessKey)

		fmt.Print("Enter AWS Region: ")
		awsRegion, _ := reader.ReadString('\n')
		awsRegion = strings.TrimSpace(awsRegion)

		// Create .aws directory if it doesn't exist
		awsDir := filepath.Dir(credentialsPath)
		if err := os.MkdirAll(awsDir, 0700); err != nil {
			fmt.Println("Error creating .aws directory:", err)
			return
		}

		// Write credentials to file
		f, err := os.Create(credentialsPath)
		if err != nil {
			fmt.Println("Error creating credentials file:", err)
			return
		}
		defer f.Close()

		_, err = f.WriteString(fmt.Sprintf("[default]\naws_access_key_id = %s\naws_secret_access_key = %s\nregion = %s\n", awsAccessKeyID, awsSecretAccessKey, awsRegion))
		if err != nil {
			fmt.Println("Error writing to credentials file:", err)
			return
		}

		fmt.Println("AWS credentials file created successfully at", credentialsPath)
	} else {
		fmt.Println("AWS credentials file found at", credentialsPath)
	}
}

// Here, you can choose the region of your bucket
func uploadFile() {
	region := "us-east-1"

	sess, err := session.NewSession(&aws.Config{
		Region: aws.String(region),
	})
	if err != nil {
		fmt.Println("Error creating session:", err)
		return
	}
	svc := s3.New(sess)

	bucket := "my-super-bucket-31289477892"
	filePath := "CLIP.txt"

	file, err := os.Open(filePath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error opening file:", err)
		return
	}
	defer file.Close()

	key := "CLIP.txt"

	// Read the contents of the file into a buffer
	var buf bytes.Buffer
	if _, err := io.Copy(&buf, file); err != nil {
		fmt.Fprintln(os.Stderr, "Error reading file:", err)
		return
	}

	// This uploads the contents of the buffer to S3
	_, err = svc.PutObject(&s3.PutObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
		Body:   bytes.NewReader(buf.Bytes()),
	})
	if err != nil {
		fmt.Println("Error uploading file:", err)
		return
	}

	fmt.Println("File uploaded successfully!!!")
}
