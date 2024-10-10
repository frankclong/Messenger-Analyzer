import api from "../api";
import Header from "../components/Header";
import LoadingIndicator from "../components/LoadingIndicator";
import { useState } from "react";
import "../styles/Form.css"

function Analyze() {
    let options = ["Test 1", "Test 2", "Test 3"]
    const [generalFormType, setGeneralFormType] = useState({});
    const [contactFormContact, setContactFormContact] = useState({});
    const [contactFormType, setContactFormType] = useState({});
    const [loading, setLoading] = useState(false);
    const [graph, setGraph] = useState(null);

    // Function to call general analysis form request
    const handleGeneralSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await api.post('/api/analysis/', generalFormType);
            setGraph(response.data.graph); // Assuming response contains a graph
        } catch (error) {
            console.error("Error submitting General form:", error);
        } finally {
            setLoading(false);
        }
    };

    // Function to call contact analysis form request
    const handleContactSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await api.post('/api/analysis/', contactFormType);
            setGraph(response.data.graph); // Assuming response contains a graph
        } catch (error) {
            console.error("Error submitting Contact form:", error);
        } finally {
            setLoading(false);
        }
    };

    function SelectOptionField({value, onChange, orderedOptions, prompt}) {
        return (
            <select 
                className="form-input"
                value={value}
                onChange={onChange}
            >
                <option value="" disabled>{prompt}</option>
                {orderedOptions.map((option, index) => (
                <option key={index} value={option}>
                    {option}
                </option>
                ))}
            </select>
        )
    }

    return (
        <div >
            <Header />
            <h2 className="text-3xl text-center">Analysis</h2>

            {/* General Form */}
            <div>
                <form onSubmit={handleGeneralSubmit} className="form-container">
                    <h3 className="mb-6 mt-6 text-xl font-semibold">General</h3>
                    <label htmlFor="options" className="block text-lg font-semibold mb-2">
                        Select an analysis type
                    </label>
                    <SelectOptionField value={generalFormType} onChange={(e) => setGeneralFormType(e.target.value)} orderedOptions={options} prompt="Select an option"/>
                    <button className="form-button" type="submit">Generate</button>
                </form>
            </div>

            {/* Contact Form */}
            <div>
                <form onSubmit={handleContactSubmit} className="form-container">
                <h3 className="mb-6 mt-6 text-xl font-semibold">Contact</h3>
                    <label htmlFor="options" className="block text-lg font-semibold mb-2">
                        Select a contact
                    </label>
                    <SelectOptionField value={contactFormContact} onChange={(e) => setContactFormContact(e.target.value)} orderedOptions={options} prompt="Select an option"/>
                    <label htmlFor="options" className="block text-lg font-semibold mb-2">
                        Select an analysis type
                    </label>
                    <SelectOptionField value={contactFormType} onChange={(e) => setContactFormType(e.target.value)} orderedOptions={options} prompt="Select an option"/>
                    <button className="form-button" type="submit">Generate</button>
                </form>
            </div>

            {loading && <LoadingIndicator/>}

            {/* Display Graph */}
            {graph && (
                <div style={{ width: '1000px', height: '100px' }}>
                    <div dangerouslySetInnerHTML={{ __html: graph }} />
                </div>
            )}
        </div>
    );
}

export default Analyze;