import Profile from "./profile/Profile";
import Menu from "./menu/Menu";
import Chat from "./chat/Chat.tsx"

export default function App() {
    return (
        <div className="App">
        <main contentEditable>
            <Profile />
            <Menu />
            <Chat />
        </main>
        <footer>
            <a href='https://github.com/marciogh/marciogh.com/'>Github source</a>
        </footer>
        </div>
    )
}