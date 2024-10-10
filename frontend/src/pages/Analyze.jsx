import api from "../api";
import Header from "../components/Header";
import LoadingIndicator from "../components/LoadingIndicator";
import { useState, useEffect } from "react";
import "../styles/Form.css"

function Analyze() {
    const [generalTypeOptions, setGeneralFormTypeOptions] = useState([]);
    const [contactTypeOptions, setContactFormTypeOptions] = useState([]);
    const [contactOptions, setContactOptions] = useState([]);

    const [isGeneral,  setGeneral] = useState(false);
    const [generalFormType,  setGeneralFormType] = useState("");
    const [selectedContact, setSelectedContact] = useState("");
    const [contactFormType, setContactFormType] = useState("");
    const [loading, setLoading] = useState(false);
    const [graph, setGraph] = useState(null);

    // Get options
    useEffect(() => {
        const getOptions = async () => {
            const res = await api.get('/api/analysis/options/')
            setGeneralFormTypeOptions(res.data['generalOptions']);
            setContactFormTypeOptions(res.data['contactOptions']);
            setContactOptions(res.data['contacts'])
        }

        getOptions()
    }, [])

    // Function to call general analysis form request
    const handleGeneralSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setGeneral(true);

        try {
            const response = await api.get('/api/analysis/generate/', {
                params: {
                    isGeneral: true, generalFormType
                }});
            console.log(response.data)
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
        setGeneral(false);

        try {
            const response = await api.get('/api/analysis/generate/', {
                params: {
                    isGeneral: false, selectedContact, contactFormType
                }});
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
                <option key={index} value={option.id}>
                    {option.value}
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
                    <SelectOptionField value={generalFormType} onChange={(e) => setGeneralFormType(e.target.value)} orderedOptions={generalTypeOptions} prompt="Select an option"/>
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
                    <SelectOptionField value={selectedContact} onChange={(e) => setSelectedContact(e.target.value)} orderedOptions={contactOptions} prompt="Select an option"/>
                    <label htmlFor="options" className="block text-lg font-semibold mb-2">
                        Select an analysis type
                    </label>
                    <SelectOptionField value={contactFormType} onChange={(e) => setContactFormType(e.target.value)} orderedOptions={contactTypeOptions} prompt="Select an option"/>
                    <button className="form-button" type="submit">Generate</button>
                </form>
            </div>

            <div className="flex flex-col items-center justify-center mx-auto my-12 p-5 max-w-md">
                {loading && <LoadingIndicator/>}
                {graph && (
                    <div style={{ width: '1000px', height: '100px' }}>
                        <div dangerouslySetInnerHTML={{ __html: graph }} />
                    </div>
                )}
            </div>
        </div>
    );
}

export default Analyze;