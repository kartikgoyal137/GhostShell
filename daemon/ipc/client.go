package ipc

import (
	"os"
	"encoding/json"
	"io"
	"fmt"
	"net"
)

type Window struct {
	Address string `json:"address"`
	Workspace WorkspaceRef `json:"workspace"`
	Class string `json:"class"`
	Title string `json:"title"`
	Focus bool `json:"focus"`
	Coord []int `json:"at"`
	Size []int `json:"size"`
}

type WorkspaceRef struct {
	ID int
	Name string 
}

func GetPath(n int) string {
	base := os.Getenv("XDG_RUNTIME_DIR")
	signature := os.Getenv("HYPRLAND_INSTANCE_SIGNATURE")
	if signature=="" {
		fmt.Println("hyprland signature not found")
		return ""
	}

	basePath := base + "/hypr/" + signature 
	socketPath := basePath + "/.socket.sock"

	if(n==2) { socketPath = basePath + "/.socket2.sock" }

	return socketPath
}

func GetWindows() ([]Window , error) {
	
	socketPath := GetPath(1)
	conn, err := net.Dial("unix", socketPath)
	if err!=nil {
		fmt.Println("unix domain socket connection failed!")
		return nil, err
	}
	defer conn.Close()

	_, err = conn.Write([]byte("j/clients"))
	if err!=nil {
		fmt.Println("failed to write into socket")
		return nil, err
	}
	data, _ := io.ReadAll(conn)
	
	var win []Window

	err = json.Unmarshal(data, &win)
	if err!=nil {
		fmt.Println("error while unmarshaling data")
		return nil , err
	}

	return win, nil
}

func Dispatch(cmd string) (string, error) {
	socketPath := GetPath(1)
	conn, err := net.Dial("unix", socketPath)
	if err!=nil {
		fmt.Println("unix domain socket connection failed")
		return "", err
	}
	defer conn.Close()

	_, err = conn.Write([]byte(cmd))
	if err!=nil {
		return "", err
	}

	out, err := io.ReadAll(conn)
	if err!=nil {
		return string(out), err
	}

	return string(out), nil
}
