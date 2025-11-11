import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');

    const onFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const onFileUpload = () => {
        const formData = new FormData();
        formData.append('file', file);
        axios.post('/api/stocks/upload', formData).then((response) => {
            setMessage('File uploaded successfully');
            console.log(response.data);
        }).catch((error) => {
            setMessage('Error uploading file');
            console.error(error);
        });
    };

    return (
        <div>
            <h2>Upload Stock List</h2>
            <input type="file" onChange={onFileChange} />
            <button onClick={onFileUpload}>Upload</button>
            <p>{message}</p>
        </div>
    );
};

export default FileUpload;
