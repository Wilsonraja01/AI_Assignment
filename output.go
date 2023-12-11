package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

type LatestParaphrase struct {
	InputText       string `json:"input_text"`
	ParaphrasedText string `json:"paraphrased_text"`
}

const (
	DatabaseUser     = "wilson1"
	DatabasePass     = "2004@w"
	DatabaseName     = "paraphrase_ai"
	DatabaseTable    = "paraphrase_golang"
	ConnectionString = DatabaseUser + ":" + DatabasePass + "@tcp(localhost:3306)/" + DatabaseName
)

func main() {
	url := "http://localhost:5000/get_latest_paraphrase"
	var prevResponse LatestParaphrase

	// Open a database connection
	db, err := sql.Open("mysql", ConnectionString)
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	for {
		latestParaphrase, err := getLatestParaphrase(url)
		if err != nil {
			fmt.Println("Error:", err)
		} else {
			if latestParaphrase.InputText != prevResponse.InputText {
				fmt.Printf("Input: %s\n", latestParaphrase.InputText)
				fmt.Printf("Output: %s\n\n", latestParaphrase.ParaphrasedText)

				// Insert into the database
				err := insertIntoDatabase(db, latestParaphrase.InputText, latestParaphrase.ParaphrasedText)
				if err != nil {
					fmt.Println("Error inserting into database:", err)
				}

				prevResponse = *latestParaphrase
			}
		}

		// Wait for a moment before making the next request
		// Adjust the sleep duration as needed
		time.Sleep(3 * time.Second)
	}
}

func getLatestParaphrase(url string) (*LatestParaphrase, error) {
	response, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}

	var latestParaphrase LatestParaphrase
	err = json.Unmarshal(body, &latestParaphrase)
	if err != nil {
		return nil, err
	}

	return &latestParaphrase, nil
}

func insertIntoDatabase(db *sql.DB, inputText, outputText string) error {
	// Prepare the SQL statement
	stmt, err := db.Prepare("INSERT INTO " + DatabaseTable + " (input, output) VALUES (?, ?)")
	if err != nil {
		return err
	}
	defer stmt.Close()

	// Execute the SQL statement
	_, err = stmt.Exec(inputText, outputText)
	if err != nil {
		return err
	}

	fmt.Println("Inserted into database:", inputText, outputText)
	return nil
}
