const startNotebook = async (gpuType) => {
  try {
    const startTime = Date.now();
    const updateInterval = setInterval(() => {
      const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
      console.log(`Starting notebook (${elapsedSeconds}s)...`);
    }, 3000);
    const response = await fetch('https://mwufi--notebook-start.modal.run', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer testingfood',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ gpu_type: gpuType })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Notebook started successfully:', data);
    clearInterval(updateInterval);
    return data;
  } catch (error) {
    console.error('Error starting notebook:', error.message);
    throw error;
  }
};

// Usage
const gpuType = process.argv[2];
if (!gpuType) {
  console.error('Please provide a GPU type as an argument.');
  process.exit(1);
}

startNotebook(gpuType)
  .then(result => {
    console.log('Notebook URL:', result.url);
    console.log('GPU Type:', result.gpu_type);
  })
  .catch(error => {
    console.error('Failed to start notebook:', error);
  });
