import { useState } from "react";
import api from "../api";
import Header from "../components/Header";
import LoadingIndicator from "../components/LoadingIndicator";
import "../styles/Form.css"

function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    
    // Handle file change
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        try {
            const res = await api.post('api/data/upload/', { file },{
                headers: {
                    "Content-Type": "multipart/form-data",
                  }
            }
            )
            setSuccess(true)
        } catch (error) {
            alert(error)
        } finally {
            setLoading(false)
        }
    };

    return (
        
      <div>
        <Header/>
        
        <div className="mt-6 px-6 py-12 bg-gray-100 rounded-xl">

            <form onSubmit={handleSubmit} className="form-container">
                <h1 className="mb-12 text-3xl text-center">Upload Zip File</h1>
                <input 
                    type="file" 
                    onChange={handleFileChange}
                    accept=".zip" // Limit file types to .zip
                    className="form-input"
                />
                {loading && <LoadingIndicator />}
                <button 
                    className="form-button" 
                    type="submit"
                >
                    Upload
                </button>
                {success && <p>Success!</p>}
            </form>

        </div>
    
      </div>
    )
}

export default Upload;