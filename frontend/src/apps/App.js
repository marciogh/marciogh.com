import Profile from "./profile/Profile";
import Menu from "./menu/Menu";
import Chat from "./chat/Chat.tsx"

export default function App() {
    return (
        <div className="App">
        <main>
            <Menu />            
            <Profile />
            <Chat />
        </main>
        </div>
    )
}