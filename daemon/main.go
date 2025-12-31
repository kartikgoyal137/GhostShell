package main

import (
	"fmt"
	"github.com/kartikgoyal137/ghostshell/server"
	"github.com/kartikgoyal137/ghostshell/ipc"
  "net/http"
	"os"
	"net"
)

func main() {
	state := ipc.NewState()

	_ , err := ipc.GetWindows()
	if err!=nil {
		fmt.Println("error fetching windows")
	}
	
	go ipc.ListenEvents(state)
	socketPath := "/tmp/ghostshell.sock"
	srv := server.NewServer(state)
	
	os.Remove(socketPath)
	listener, err := net.Listen("unix", socketPath)
	os.Chmod(socketPath, 0600)
	defer listener.Close()

  http.Serve(listener, srv.Mux)

	select{}

}
