package server

import (
	"net/http"
	"encoding/json"
	"github.com/kartikgoyal137/ghostshell/ipc"

)

type Server struct {
	Mux *http.ServeMux
	State *ipc.State
}

type CmdReq struct {
	Cmd string `json:"command"`
}

func NewServer(state *ipc.State) *Server {
	s := &Server{
		Mux: http.NewServeMux(),
		State: state,
	}

	s.routes()

	return s
}

func (s *Server) routes()  {
	s.Mux.HandleFunc("/state", s.handleState)
	s.Mux.HandleFunc("/dispatch", s.handleDispatch)
}

func (s *Server) handleState(w http.ResponseWriter, r *http.Request) {
 w.Header().Set("Content-Type", "application/json")
 s.State.Mu.RLock()
 defer s.State.Mu.RUnlock()

 json.NewEncoder(w).Encode(s.State)
}

func (s *Server) handleDispatch(w http.ResponseWriter, r *http.Request) {
	var req CmdReq
  if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
    http.Error(w, err.Error(), http.StatusBadRequest)
		return
  }

  output, err := ipc.Dispatch(req.Cmd)
  w.Header().Set("Content-Type", "application/json")
    if err != nil {
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(map[string]string{
            "status": "error",
            "message": err.Error(),
            "output": output,
        })
        return
    }

    json.NewEncoder(w).Encode(map[string]string{
        "status": "ok",
        "output": output,
    })

}
