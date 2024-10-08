let translations = null
function make_notification(state, text) {
    svg = "";
    if (state === "good")
        svg = `<svg version="1.1" style="width:3em;margin-right:1em" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
                viewBox="0 0 17.837 17.837" xml:space="preserve">
                <g>
                    <path style="fill:#59c428;" d="M16.145,2.571c-0.272-0.273-0.718-0.273-0.99,0L6.92,10.804l-4.241-4.27
		c-0.272-0.274-0.715-0.274-0.989,0L0.204,8.019c-0.272,0.271-0.272,0.717,0,0.99l6.217,6.258c0.272,0.271,0.715,0.271,0.99,0
		L17.63,5.047c0.276-0.273,0.276-0.72,0-0.994L16.145,2.571z" />
                </g>
            </svg>`
    else if (state === "bad")
        svg = `<svg viewBox="0 0 24 24" style="width:3em;margin-right:1em" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M2.20164 18.4695L10.1643 4.00506C10.9021 2.66498 13.0979 2.66498 13.8357 4.00506L21.7984 18.4695C22.4443 19.6428 21.4598 21 19.9627 21H4.0373C2.54022 21 1.55571 19.6428 2.20164 18.4695Z"
                    stroke="#F00000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M12 9V13" stroke="#F00000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M12 17.0195V17" stroke="#F00000" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round" />
            </svg>`
    return $(`<article style="display: none;"><div>${svg}${text}</div></article>`)
}
function send_config(callback_if_success = null) {
    let modules_states = {}
    $("#on-off-modules").children("label").each((_, label) => {
        let element = $(label).children("input").get(0)
        modules_states[element.id.slice(7)] = element.checked
    })
    fetch("/set-config", {
        method: "POST",
        body: JSON.stringify({
            language: $("#language").val(),
            assistant_name: $("#assistant_name").val(),
            assistant_gender: $("#assistant_gender").val(),
            assistant_voice_key: $("#assistant_voice_key").val(),
            assistant_voice_rate: $("#assistant_voice_rate").val(),
            vosk_model: $("#vosk_model").val(),
            vosk_debug: $("#vosk_debug").is(":checked"),
            use_chat: $("#use_chat").is(":checked"),
            gpt_model: $("#gpt_model").val(),
            use_openai_gpt: $("#use_openai_gpt").is(":checked"),
            use_openai_tts: $("#use_openai_tts").is(":checked"),
            openai_tts_model: $("#openai_tts_model").val(),
            gpt_info: $("#gpt_info").val(),
            modules_states: modules_states,
            intention_best_proba: $("#intention_best_proba").val(),
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then(response => response.json()).then(data => {
        if (data.result !== null && data.result === "ok") {
            // translations["The AI configuration saved successfully."]
            let text = "The AI configuration saved successfully."
            if (translations !== null)
                text = translations[text]
            addToStack("notifications-stack", make_notification("good", text), 3000)
            if (callback_if_success !== null)
                callback_if_success()
        }
        else {
            let text = "Some error occured while trying to save the configuration:"
            // translations["Some error occured while trying to save the configuration:"]
            if (translations !== null)
                text = translations[text]
            addToStack("notifications-stack", make_notification("bad", text + ` ${data.reason}`), 3000)
        }
    }).catch(reason => {
        // translations["Some error occured while trying to save the configuration:"]
        let text = "Some error occured while trying to save the configuration:"
        if (translations !== null)
            text = translations[text]
        addToStack("notifications-stack", make_notification("bad", text + ` ${reason}`), 3000)
    })
}
function reset_ai() {
    fetch("/reset-ai", {
        method: "POST"
    }).then(response => response.json()).then(data => {
        if (data.result !== null && data.result === "ok") {
            // translations["The AI reset successfully. No data or configuration stored."]
            let text = "The AI reset successfully. No data or configuration stored."
            if (translations !== null)
                text = translations[text]
            addToStack("notifications-stack", make_notification("good", text), 3000)
            setTimeout(() => {
                window.location.reload()
            }, 4000)
        }
        else {
            // translations["Some error occured while trying to reset AI:"]
            let text = "Some error occured while trying to reset AI:"
            if (translations !== null)
                text = translations[text]
            addToStack("notifications-stack", make_notification("bad", text + ` ${data.reason}`), 3000)
        }
    }).catch(reason => {
        // translations["Some error occured while trying to reset AI:"]
        let text = "Some error occured while trying to reset AI:"
        if (translations !== null)
            text = translations[text]
        addToStack("notifications-stack", make_notification("bad", text + ` ${reason}`), 3000)
    })
}
function run_ai() {
    send_config(() => {
        window.location.assign("/run-ai")
    })
}
function fillSelect(url_to_fetch, select_id) {
    fetch(url_to_fetch).then((response) => response.json()).then((data) => {
        const select = document.getElementById(select_id)
        data.forEach(opt => {
            let option = document.createElement('option')
            option.value = opt
            option.innerHTML = opt
            select.appendChild(option)
        })
    })
}
function fillGPTSelect() {
    fetch("/gpt-models").then(response => response.json()).then(data => {
        const select = document.getElementById("gpt_model")
        data.forEach(model => {
            let option = document.createElement('option')
            option.value = model.filename
            let inner = model.name
            if (model.loaded == true)
                inner += " - (loaded)"
            option.innerHTML = inner
            select.appendChild(option)
        })
    })
}
fetch("/translations").then(response => response.json()).then(data => {
    translations = data
})
fillSelect("/languages", "language")
fillSelect("/voice-keys", "assistant_voice_key")
fillSelect("/vosk-models", "vosk_model")
fillGPTSelect()
fetch("/avaliable-modules").then(response => response.json()).then(data => {
    const fieldset = $("#on-off-modules")
    for (const [key, value] of Object.entries(data)) {
        let field = $(`<label for="module_${key}">
                            <input type="checkbox" id="module_${key}" name="module_${key}" role="switch">
                           ${translations[value] === undefined ? value : translations[value]}
                        </label>`)
        fieldset.append(field.get())
    }
})
fetch("/previous-config").then((response) => response.json()).then((data) => {
    for (const [key, value] of Object.entries(data)) {
        element = document.getElementById(key)
        if (element === null)
            continue
        if (element.tagName === "INPUT" && element.type === "checkbox")
            element.checked = value
        else
            element.value = value
    }
    if (data.found_openai_token === false)
        $("article#openai_key_invalid").show()
    if (data.have_openai_services_connection === false)
        $("article#openai_no_connection").show()
    for (const [key, value] of Object.entries(data.modules_states)) {
        element = document.getElementById(`module_${key}`)
        if (element === null)
            continue
        element.checked = value
    }
})