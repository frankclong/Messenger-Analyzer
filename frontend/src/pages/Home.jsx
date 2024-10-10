import Header from "../components/Header";
import Analyze from "./Analyze";
import { Navigate } from "react-router-dom";

function Home() {
    return (
      <Navigate to="/analyze" />
    )
}

export default Home;