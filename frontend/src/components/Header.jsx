import {React} from 'react';
import { Link, useNavigate} from 'react-router-dom';
import useAuth from '../useAuth';
import api from '../api';

function Header() {
    const { isAuthorized } = useAuth();
    const navigate = useNavigate();

    const tryDeleteData = async () => {
        try {
            const res = await api.delete('api/data/delete/')
            console.log(res)
            navigate(0);
        } catch (error) {
            console.log(error)
            alert(error)
        }
    };

    return (
        <nav className="py-6 px-6 flex justify-between items-center border-b border-gray-200">
        <Link to="/" className="text-xl font-semibold">Messenger Analyzer</Link>

        <div className="space-x-6">
            {isAuthorized ? (
            <>
                <Link to="/upload" className="px-6 py-3 text-lg font-semibold bg-blue-500 text-white rounded-xl hover:bg-blue-700">Upload Data</Link>
                {/* <Link to="/clean" className="px-6 py-3 text-lg font-semibold bg-blue-300 text-white rounded-xl hover:bg-blue-500">Clean Data</Link> */}
                <Link to="#" 
                    onClick={(e) => {
                        e.preventDefault();
                        tryDeleteData();
                    }} 
                    className="px-6 py-3 text-lg font-semibold bg-red-500 text-white rounded-xl hover:bg-red-700">Delete Data</Link>
                <Link to="/logout" className="px-6 py-3 text-lg font-semibold bg-blue-500 text-white rounded-xl hover:bg-blue-700">Logout</Link>
            </>
            ) : (
            <>
                <Link to="/register" className="px-6 py-3 text-lg font-semibold bg-blue-500 text-white rounded-xl hover:bg-blue-700">Sign up</Link>
                <Link to="/login" className="px-6 py-3 text-lg font-semibold bg-blue-500 text-white rounded-xl hover:bg-blue-700">Log in</Link>
            </>
            )}
        </div>
        </nav>
    );
};

export default Header;