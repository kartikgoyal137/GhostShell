package main

import (
	"fmt"
	"github.com/kartikgoyal137/ghostshell/ipc"
	"time"
)

func main() {
	state := ipc.NewState()

	win, err := ipc.GetWindows()
	if err!=nil {
		fmt.Println("error fetching windows")
	}

	for i,v := range win {
		fmt.Println(i)
		fmt.Println(v.Title)
	}
	
	go ipc.ListenEvents(state)

	for {
		state.Mu.RLock()
		fmt.Printf("Current Workspace: %d | Windows Open: %d\n", state.Active, len(state.Win))
		state.Mu.RUnlock()
		time.Sleep( 2 * time.Second)
	}

	select{}

}
