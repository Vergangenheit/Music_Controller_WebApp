import React, { Component } from "react";
import { Grid, Button, Typography, unstable_createMuiStrictModeTheme, ButtonGroup, ThemeProvider } from "@material-ui/core";
import { Link } from "react-router-dom";
import CreateRoomPage from "./CreateRoomPage";

export default class Room extends Component {
  constructor(props) {
    super(props);
    this.state = {
      votesToSkip: 2,
      guestCanPause: false,
      isHost: false,
      showSettings: false,
      spotifyAuthenticated: false,
    };
    this.roomCode = this.props.match.params.roomCode;
    
    this.leaveButtonPressed = this.leaveButtonPressed.bind(this);
    this.updateShowSettings = this.updateShowSettings.bind(this);
    this.renderSettingsButton = this.renderSettingsButton.bind(this);
    this.renderSettings = this.renderSettings.bind(this);
    this.getRoomDetails = this.getRoomDetails.bind(this);
    this.authenticateSpotify = this.authenticateSpotify.bind(this);
    this.getRoomDetails();
  }

  getRoomDetails() {
    fetch("/api/get-room" + "?code=" + this.roomCode)
      .then((response) => {
        if(!response.ok) {
          this.props.leaveRoomCallback();
          this.props.history.push("/");
        }
        return response.json();
      })
      .then((data) => {
        this.setState({
          votesToSkip: data.votes_to_skip,
          guestCanPause: data.guest_can_pause,
          isHost: data.is_host,
        });
        if (this.state.isHost) {
          this.authenticateSpotify();
        }
      });
  }

  authenticateSpotify() {
    // send a request to be to ask if user is authenticated but only when user is a host, 
    // therefore we have to wait for getRoomDetails to return
    fetch('/spotify/is-authenticated').then((response) => response.json()).then((data) => {
      this.setState({ spotifyAuthenticated: data.is_auth });
      // if the user is not authenticated we need to auth them
      if (!data.is_auth) {
        fetch('/spotify/get-auth-url').then((response) => response.json())
        .then((data) => {
          // redirects us to the spotify authorization page
          window.location.replace(data.url);
        });
      }
    });
  }

  leaveButtonPressed() {
    //call leave room endpoint
    const requestOptions = {
      method: "POST",
      header: {"Content-Type": "application/json"},
    };
    fetch("/api/leave-room", requestOptions).then((_response) => {
      this.props.leaveRoomCallback();
      this.props.history.push("/");
    });
  }

  updateShowSettings(value) {
    this.setState({
      showSettings: value,
    });
  }

  renderSettings() { // inside we will use CreateRoomPage component passing some props to it
    return (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <CreateRoomPage update={true} votesToSkip={this.state.votesToSkip} guestCanPause={this.state.guestCanPause}
        roomCode={this.roomCode}
        updateCallback={this.getRoomDetails} />
      </Grid>
      <Grid item xs={12} align="center">
        <Button variant="contained"
        color="secondary"
        onClick={() => this.updateShowSettings(false)}>
          Close
        </Button>
      </Grid>
    </Grid>
    )
  }

  // let's made a method to render the button to update the value
  renderSettingsButton() {
    return (
    <Grid item xs={12} align="center">
      <Button variant="contained" color="primary" onClick={() => this.updateShowSettings(true)}>
        Settings
      </Button>
    </Grid>
    )
  }

  render() {
    // render the content only when we're not showing the settings page
    if (this.state.showSettings) {
      return this.renderSettings();
    }
    return (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <Typography variant="h4" component="h4">
            Code: {this.roomCode}
          </Typography>
        </Grid>
        <Grid item xs={12} align="center">
          <Typography variant="h6" component="h6">
            Votes: {this.state.votesToSkip}
          </Typography>
        </Grid>
        <Grid item xs={12} align="center">
          <Typography variant="h6" component="h6">
            Guest Can Pause: {this.state.guestCanPause.toString()}
          </Typography>
        </Grid>
        <Grid item xs={12} align="center">
          <Typography variant="h6" component="h6">
            Host: {this.state.isHost.toString()}
          </Typography>
        </Grid>
        {this.state.isHost ? this.renderSettingsButton() : null}
        <Grid item xs={12} align="center">
          <Button
            variant="contained"
            color="secondary"
            onClick={this.leaveButtonPressed}
          >
            Leave Room
          </Button>
        </Grid>
      </Grid>






      // <div>
      //   <h3>{this.roomCode}</h3>
      //   <p>Votes: {this.state.votesToSkip}</p>
      //   <p>Guest Can Pause: {this.state.guestCanPause.toString()}</p>
      //   <p>Host: {this.state.isHost.toString()}</p>
      // </div>
    );
  }
}