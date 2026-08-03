func serve(req *http.Request) {
    data, _ := os.ReadFile(req.URL.Query().Get("file"))
    w.Write(data)
}
