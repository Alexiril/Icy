let len = 0
setInterval(() => {
    fetch("/messages").then(response => response.json()).then(data => {
        $("#messages").html("")
        data.forEach(element => {
            const content = element.content
            const role = element.role === "assistant" ? "bot-message" : "user-message"
            const e = $(`<div class="container message-container ${role}">${content}</div>`)
            $("#messages").append(e)
        })
        if (data.length != len) {
            $("#messages").scrollTop(function() { return this.scrollHeight; });
        }
        len = data.length
    })
}, 1000)