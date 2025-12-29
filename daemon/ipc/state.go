package ipc

import (
	"sync"
	"fmt"
	"strconv"
)

type State struct {
	Mu sync.RWMutex
	Win map[string]Window
	Active int
}

func NewState() *State {
	return &State {
		Win: make(map[string]Window),
	}
}

func (s *State) RefreshWindows() {
	win, err := GetWindows()
	if err!=nil {
		fmt.Println("failed to fetch windows")
	}

	s.Mu.Lock()

	s.Win = make(map[string]Window)

	for _ , v := range win {
		s.Win[v.Address] = v
	}

	s.Mu.Unlock()

}

func (s *State) SetWorkspace(cmd []string) {
	id, _ := strconv.Atoi(cmd[1])
	s.Mu.Lock()
	s.Active = id
	s.Mu.Unlock()
}
