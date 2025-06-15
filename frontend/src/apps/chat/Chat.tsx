import { JSX, useState } from "react";
import "./chat.css";
import showdown from "showdown";
import DOMPurify from 'dompurify'

const converter = new showdown.Converter();
    
const BACKEND = "https://fqc0a78xlj.execute-api.ap-southeast-2.amazonaws.com/test"

export default function Chat(): JSX.Element {

    const [spinner, setSpinner] = useState(false);
    const [lastResponse, setLastResponse] = useState<string>("");
    const [responses, setResponses] = useState<string[]>([]);
    const [questions, setQuestions] = useState<string[]>([]);
    const [responseFadeIn, setResponseFadeIn] = useState<boolean>();
    const [lastError, setLastError] = useState<string>("");
    const [q, setQ] = useState<string>("");

    function onFormSubmit(e) {
        e.preventDefault();
        ask()
    }

    function ask() {
        if (q.length > 0) {
            setSpinner(true);
            setLastError("")
            setQ("")
            if (lastResponse != "") {
                setResponses([...responses, lastResponse]);
            }
            setResponseFadeIn(false);
            fetch(BACKEND + "?q=" + encodeURIComponent(q))
                .then((response) => {
                    if (response.status === 429) {
                        setSpinner(false);
                        setLastError("To many questions, come back later");
                    } else {
                        response.json().then((data) => {
                            const html = converter.makeHtml(data);
                            setSpinner(false);
                            setResponseFadeIn(true);
                            setQuestions([q, ...questions])
                            setResponses([html, ...responses]);
                        })
                    }
                })
                .catch((error) => {
                    setSpinner(false);
                    setLastError(error);
                    console.log(lastError);
                });
        }
    }

    return (
        <div className="Chat">
            <div className="spinnerContainer">
            <div className={spinner? "fadeIn" : "fadeOut"}>Thinking...</div>
            </div>
            <form onSubmit={onFormSubmit}>
                <h1>Ask me anything</h1>
                <input autoFocus type="text" name="q" value={q} onChange={e => setQ(e.target.value)}/>
            </form>
            {lastResponse?<span
                className={responseFadeIn? "responseFadeIn" : "responseFadeOut"}
                dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(lastResponse)}}
            />: null
            }
            {responses.map(r => (
                <span className="responseFadeIn"
                    dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(r)}}
                />
            ))}
            </div>
    )
}