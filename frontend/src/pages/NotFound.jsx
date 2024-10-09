import Header from "../components/Header";

function NotFound() {
    return <div className="justify-center h-screen">
        <Header />
        <h1 className="m-6 text-3xl font-bold text-center">404 Not Found</h1>
        <p className="text-center">The page you're looking for doesn't exist!</p>
    </div>
}

export default NotFound;