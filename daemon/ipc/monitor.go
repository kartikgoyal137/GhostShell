package ipc

import (
	"fmt"
	"bufio"
	"net"
	"strings"
)

func ListenEvents(state *State) error {
	socketPath := GetPath(2)
	conn, err := net.Dial("unix", socketPath)
	if err!=nil {
		fmt.Println("failed to connect to socket")
		return nil
	}

	scanner := bufio.NewScanner(conn)

	for scanner.Scan() {
		cmd := strings.Split(scanner.Text(), ">>")
		if(cmd[0]=="workspace") {
			state.SetWorkspace(cmd)
		}	else {
			state.RefreshWindows()
		}

	}

	return nil
} 
