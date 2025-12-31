package main

import (
	"github.com/kartikgoyal137/ghostshell/server"
	"github.com/kartikgoyal137/ghostshell/ipc"
  "net/http"
	"os"
	"fmt"
	"net"
)

func main() {
	state := ipc.NewState()

	state.RefreshWindows()
	
	go ipc.ListenEvents(state)
	socketPath := "/tmp/ghostshell.sock"
	srv := server.NewServer(state)
	
	os.Remove(socketPath)
	listener, err := net.Listen("unix", socketPath)
  if err!=nil {
			fmt.Println("failed to setup listner")
			return
	}

	os.Chmod(socketPath, 0600)
	defer listener.Close()

  http.Serve(listener, srv.Mux)

	select{}

}
