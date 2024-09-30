const convertToLocalTimezone = (utcDateString) => {
  const utcDate = new Date(utcDateString);
  const cdtOffset = -5; // CDT is UTC-5

  // Create a new date object with the adjusted time
  const cdtDate = new Date(utcDate.getTime() + cdtOffset * 60 * 60 * 1000);

  // Format the date string
  const options = {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Chicago',
  };

  const formattedDate = cdtDate.toLocaleString('en-US', options);
  const [date, time] = formattedDate.split(', ');
  const [month, day, year] = date.split('/');
  
  return `${month}/${day}/${year} ${time}`;
};


const getNotebooks = async () => {
  try {
    const response = await fetch('https://mwufi--notebook-get-notebooks.modal.run');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const notebooks = data.notebooks;

    if (Object.keys(notebooks).length === 0) {
      console.log('\x1b[33mNo active notebooks found.\x1b[0m');
      return;
    }

    console.log('\x1b[36m' + '='.repeat(80) + '\x1b[0m');
    console.log('\x1b[36mActive Notebooks:\x1b[0m');
    console.log('\x1b[36m' + '='.repeat(80) + '\x1b[0m');

    for (const [url, details] of Object.entries(notebooks)) {
      const createdAt = convertToLocalTimezone(details.created_at);
      console.log('\x1b[32mURL: ' + url + '\x1b[0m');
      console.log('\x1b[33mCreated At: ' + createdAt + '\x1b[0m');
      console.log('\x1b[36m' + '-'.repeat(80) + '\x1b[0m');
    }

    console.log('\x1b[35m\nTo copy a URL, select and right-click (or use Cmd+C on Mac, Ctrl+C on Windows).\x1b[0m');
  } catch (error) {
    console.error('\x1b[31mError fetching notebooks:', error.message, '\x1b[0m');
  }
};

getNotebooks();
