package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"io/ioutil"
	"net/http"
	"time"
)

type LatestParaphrase struct {
	InputText       string `json:"input_text"`
	ParaphrasedText string `json:"paraphrased_texts"`
}

const (
	apiUrl           = "http://localhost:5000/get_latest_paraphrase"
	DatabaseUser     = "wilson1"
	DatabasePass     = "2004@w"
	DatabaseName     = "paraphrase_ai"
	DatabaseTable    = "paraphrase_golang"
)

func main() {
	var prevResponse LatestParaphrase

	// Open a connection to the database
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@/%s", DatabaseUser, DatabasePass, DatabaseName))
	if err != nil {
		fmt.Println("Error opening database:", err)
		return
	}
	defer db.Close()

	for {
		latestParaphrase, err := getLatestParaphrase(apiUrl)
		if err != nil {
			fmt.Println("Error:", err)
		} else {
			if latestParaphrase.InputText != prevResponse.InputText ||
				latestParaphrase.ParaphrasedText != prevResponse.ParaphrasedText {
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

func insertIntoDatabase(db *sql.DB, input, output string) error {
	// Prepare the SQL statement
	stmt, err := db.Prepare("INSERT INTO " + DatabaseTable + "(input, output) VALUES (?, ?)")
	if err != nil {
		return err
	}
	defer stmt.Close()

	// Execute the prepared statement
	_, err = stmt.Exec(input, output)
	if err != nil {
		return err
	}

	fmt.Println("Inserted into database:", input, output)
	return nil
}
