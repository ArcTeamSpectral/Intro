const deleteNotebook = async (url) => {
  try {
    const response = await fetch('https://mwufi--notebook-stop.modal.run', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer testingfood',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ notebook_url: url })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting notebook:', error.message);
    throw error;
  }
};

// Usage
const notebookUrl = process.argv[2];
if (!notebookUrl) {
  console.error('Please provide a notebook URL as an argument.');
  process.exit(1);
}

deleteNotebook(notebookUrl)
  .then(result => {
    console.log('Deletion result:', result);
  })
  .catch(error => {
    console.error('Failed to delete notebook:', error);
  });
