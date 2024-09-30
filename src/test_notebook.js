const startNotebook = async () => {
  try {
    const response = await fetch('https://mwufi--notebook-start-dev.modal.run', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer testingfood',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Notebook started successfully:', data);
    return data;
  } catch (error) {
    console.error('Error starting notebook:', error.message);
    throw error;
  }
};

// Usage
startNotebook()
  .then(result => {
    console.log('Notebook URL:', result.url);
    console.log('GPU Type:', result.gpu_type);
  })
  .catch(error => {
    console.error('Failed to start notebook:', error);
  });

