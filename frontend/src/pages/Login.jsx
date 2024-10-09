import Form from "../components/Form";
import Header from "../components/Header";

function Login() {
    return (
        <div>
        <Header/>
        <Form route="api/token/" method="login" />
        </div>
    )
}

export default Login;