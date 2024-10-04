// import logo from './logo.svg';
// import './App.css';

import axios from 'axios'
import React from 'react'

class App extends React.Component {
  state = { details : [],}
  componentDidMount() {
    let data;
    axios.get('http://localhost:8000/api')
    .then(res => {
      console.log(res)
      data = res.data;
      this.setState({
        details: data
      });
    })
    .catch(err => {})
  }

  render() {
    return (
      <div>
        <header>Data Generated From Django</header>
        <hr></hr>
        {this.state.details.map((output, id) => (
          <div key={output.id}>
            <div>
              <h2>{output.title}</h2>
              <h3>{output.body}</h3>
            </div>
          </div>
        ))}
      </div>
    )
  }
}

// function App() {
//   return (
//     <div className="App">
//       <div>
//         <h1>Messenger Analyzer</h1>
//       </div>
//     </div>
//   );
// }

export default App;
