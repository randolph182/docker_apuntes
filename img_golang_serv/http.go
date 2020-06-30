package main

import (
        "fmt"
        "log"

        "encoding/json"
        "io/ioutil"
        "net/http"
        "github.com/nats-io/nats.go"
)

type datosRecibidos struct {
        Nombre        string `json:"name"`
        Departamento  string `json:"depto"`
        Edad          int    `json:"age"`
        FormaContagio string `json:"form"`
        Estado        string `json:"state"`
}

func main() {
        mux := http.NewServeMux()
        mux.HandleFunc("/datos", datos)
        mux.HandleFunc("/",hm)
        log.Printf("listening on port 8080")
        log.Fatal(http.ListenAndServe(":8080", mux))
}


func hm(w http.ResponseWriter, r *http.Request){
        fmt.Fprintf(w, "hola mundo from json ")
}

func datos(w http.ResponseWriter, r *http.Request) {
        if r.Method == "POST" {
                //var results []string
                body, err := ioutil.ReadAll(r.Body)
                if err != nil {
                        fmt.Println("Error reading request body", http.StatusInternalServerError)
                }
                //results = append(results, string(body))
                dat := datosRecibidos{}
                err = json.Unmarshal(body, &dat)
                if err != nil {
                        fmt.Println("Error al convertir los datos: %s", err)
                        w.Write([]byte(err.Error()))
                }
                //====== TRABAJANDO CON NATS ===============================
                nc, err := nats.Connect("http://35.223.171.148:4222")
                if err != nil {
                        log.Fatal(err)
                }
                defer nc.Close()

                ec, err := nats.NewEncodedConn(nc, nats.JSON_ENCODER)

                if err != nil {
                        log.Fatal(err)
                }
                defer ec.Close()

                // Publish the message
                if err := ec.Publish("updates", &dat); err != nil {
                        log.Fatal(err)
                }

                //fmt.Println(dat.Nombre)
                fmt.Println(dat)
        } else {
                http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
                fmt.Print("error")
        }
}

