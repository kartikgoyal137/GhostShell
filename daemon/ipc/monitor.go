package ipc

import (
	"fmt"
	"bufio"
	"net"
	"strings"
	"time"
)

func ListenEvents(state *State) error {
	for {
		socketPath := GetPath(2)
		conn, err := net.Dial("unix", socketPath)
		if err != nil {
		  fmt.Println("Waiting for Hyprland event socket...") 
			time.Sleep(2 * time.Second)
			continue
		}

		fmt.Println("Connected to Hyprland event socket")
		processConnection(conn, state)
		
		conn.Close()
		fmt.Println("Event socket connection lost. Reconnecting...")
		time.Sleep(1 * time.Second)
	}
}

func processConnection(conn net.Conn, state *State) {
	scanner := bufio.NewScanner(conn)

	for scanner.Scan() {
		text := scanner.Text()
		cmd := strings.Split(text, ">>")

		if len(cmd) < 1 {
			continue
		}

		if cmd[0] == "workspace" {
			state.SetWorkspace(cmd)
		} else {
			state.RefreshWindows()
		}
	}
}
