import Form from "../components/Form";
import Header from "../components/Header";

function Register() {
    return (
    <div>
        <Header />
        <Form route="api/user/register/" method="register" />
    </div>
    )
}

export default Register;