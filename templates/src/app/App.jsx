import React, { Component } from 'react';
import axios from 'axios';

class App extends Component {
  constructor(props){
    super();
    this.state = {
      oauthUrl: "",
      firstName: "",
      lastName: "",
      authenticated: false
    };

    this.initiateOauth = this.initiateOauth.bind(this);
  }

  componentDidMount(){
    this.initiateOauth();
  }

  initiateOauth(){
    axios.get('/api/userinfo')
      .then(response => {
        if(response.data.userinfo){
          console.log("USR INFO IS: ", response.data.userinfo);
        } else if(response.data.signin_url){
          console.log("SIGNINURL IS: ", response.data.signin_url);
          this.setState({
            oauthUrl: response.data.signin_url
          });
        }
      })
      .catch(err => console.log("ERROR FROM PYTHON SERVER IS: ", err));
  }



  render(){
    return this.state.authenticated === false ? (
      <div>
        <h1 className="welcome">Hello From The App Component</h1>
        <button onClick={(e) => {e.preventDefault(); this.initiateOauth()}}>Signin With Capital One</button>
      </div>
    ) :
    (
      <div>
        <h1>Hello, {this.state.firstName} {this.state.lastName}</h1>
      </div>
    )
  }
}


export default App;
