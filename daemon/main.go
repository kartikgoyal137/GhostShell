package main

import (
	"fmt"
	"github.com/kartikgoyal137/ghostshell/server"
	"github.com/kartikgoyal137/ghostshell/ipc"
  "net/http"
)

func main() {
	state := ipc.NewState()

	_ , err := ipc.GetWindows()
	if err!=nil {
		fmt.Println("error fetching windows")
	}
	
	go ipc.ListenEvents(state)

	srv := server.NewServer(state)
  http.ListenAndServe(":8080", srv.Mux)

	select{}

}
