/* SERVER */
#include <stdio.h>  
#include <string.h> //strlen  
#include <stdlib.h>  
#include <errno.h>  
#include <unistd.h> //close  
#include <arpa/inet.h> //close  
#include <sys/types.h>  
#include <sys/socket.h>  
#include <netinet/in.h>  
#include <sys/time.h> //FD_SET, FD_ISSET, FD_ZERO macros  
#include <iostream>
#include <fstream>
#include "message.h"
#define TRUE 1  
#define FALSE 0  
#define PORT 8080

using namespace std;

union uMessage {
    init_message init_msg;
    coord_message coord_msg;
    start_message start_msg;
    status_message status_msg;
    coords_ok_message coords_ok;
    drone_at_waypoint drone_wp;
    abort_message abort_msg;
    image_message image_msg;
};
void init_struct(int socket, char* ip, int port, init_message* msg_ptr, 
                 struct client* drone, struct client* img_pro, 
                 struct client* main_prog);
void send_message(uMessage* msg_ptr, struct client* drone, 
                  struct client* img_pro, struct client* main_prog, 
                  size_t size, char receiver);


struct client {
    bool init_bool;
    char* ip_address;
    int port;
    int sock_fd;
};


int main(int argc , char *argv[]) {   
    //Set init-flag to false for all clients
    client* drone = new client();
    drone->init_bool = false;

    client* img_pro = new client();
    img_pro->init_bool = false;

    client* main_prog = new client();
    main_prog->init_bool = false;

    int opt = TRUE;
    int master_socket, addrlen, new_socket, client_socket[5], max_clients = 5, 
        activity, i, valread, sd;   
    int max_sd;   
    struct sockaddr_in address;   
	
    //Data buffer of 1K  
    char buffer[1025];  

    //Set of socket descriptors  
    fd_set readfds;   
    FD_ZERO(&readfds);

    //Hello message from server
    char* message_server = "Hejsan mvh Server <3\n";

    //Initialise all client_socket[] to 0 so not checked  
    for (i = 0; i < max_clients; i++) {
        client_socket[i] = 0;   
    }   

    //Create a master socket  
    if ((master_socket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {   
        perror("socket failed");   
        exit(EXIT_FAILURE);   
    }   

    //Set master socket to allow multiple connections 
    if (setsockopt(master_socket, SOL_SOCKET, SO_REUSEADDR, (char*) &opt, 
                   sizeof(opt)) < 0) {   
        perror("setsockopt");   
        exit(EXIT_FAILURE);   
    }   

    //Type of socket created  
    address.sin_family = AF_INET;   
    address.sin_addr.s_addr = INADDR_ANY;   
    address.sin_port = htons( PORT );   

    //Bind the socket to localhost port 8080 (defined at the top of the file)
    if (bind(master_socket, (struct sockaddr*) &address, sizeof(address)) < 0) {   
        perror("bind failed");   
        exit(EXIT_FAILURE);   
    }   
    cout << "Listener on port " << PORT << endl;   

    //Try to specify maximum of 3 pending connections for the master socket  
    if (listen(master_socket, 3) < 0) {   
        perror("listen");   
        exit(EXIT_FAILURE);   
    }   

    //Accept the incoming connection  
    addrlen = sizeof(address);   
    cout << "Waiting for connections ..." << endl;   

    while (true) {
        //Clear the socket set  
        FD_ZERO(&readfds);   

        //Add master socket to set  
        FD_SET(master_socket, &readfds);   
        max_sd = master_socket;   

        //Add child sockets to set  
        for (i = 0; i < max_clients; i++) {   
            //Socket descriptor  
            sd = client_socket[i];   

            //If valid socket descriptor then add to read list  
            if (sd > 0) FD_SET(sd, &readfds);   

            //Highest file descriptor number, need it for the select function  
            if (sd > max_sd) max_sd = sd;   
        }   

        /*
         *Wait for an activity on one of the sockets, timeout is NULL,  
         *so wait indefinitely  
         */
        activity = select( max_sd + 1 , &readfds , NULL , NULL , NULL);   
        if ((activity < 0) && (errno!=EINTR)) {   
            cout << "Error while running \"select\"" << endl;   
        }   

        /*
         *If something happened on the master socket,  
         *then it is an incoming connection  
         */
        if (FD_ISSET(master_socket, &readfds)) {   
            if ((new_socket = accept(master_socket, (struct sockaddr*) &address, 
                                     (socklen_t*) &addrlen)) < 0) {   
                perror("accept");   
                exit(EXIT_FAILURE);   
            }   
    
            //Print socket number - used in send and receive commands  
            cout << "New connection , socket fd is " << new_socket << 
                " , ip is: " << inet_ntoa(address.sin_addr) << 
                " , port : " << ntohs(address.sin_port) << endl;
    
            //Send new connection greeting message  
            if (send(new_socket, message_server, strlen(message_server), 0) != 
                strlen(message_server)) {
                perror("send");   
            }   
    
            cout << "Welcome message sent successfully" << endl;   
    
            //Add new socket to array of sockets  
            for (i = 0; i < max_clients; i++) {   
                //If position is empty, add socket  
                if (client_socket[i] == 0) {   
                    client_socket[i] = new_socket;   
                    cout << "Adding to list of sockets as " << i << endl;   
                            
                    break;   
                }   
            }
    
        }   
        //If an IO operation happens on a socket 
        for (i = 0; i < max_clients; i++) {   
            sd = client_socket[i];   

            if (FD_ISSET(sd, &readfds)) {  
                /*
                 *Check if it was for closing socket, and also read the  
                 *incoming message  
                 */
                if ((valread = read(sd,  buffer, 1024)) == 0) {   
                    //Somebody disconnected , get his details and print  
                    getpeername(sd, (struct sockaddr*) &address, 
                                (socklen_t*) &addrlen);
                    cout << "Host disconnected , ip" << 
                        inet_ntoa(address.sin_addr) << " , port " 
                         << ntohs(address.sin_port) << " socket " << sd << endl;                         

                    //Close the socket and mark as 0 in list for reuse
                    close(sd);   
                    client_socket[i] = 0;   
                }   

                //Check type of message and from whom
                else {   
                    /*
                     *Set the string - terminating NULL byte on the end  
                     *of the data read
                     */
                    buffer[valread] = '\0';
                    uMessage* msg = new uMessage();
                    cout << "The message type is " << ((int*)buffer)[0] << endl;
                    /*
                     *Look at the message what type of messsage it is, who it is
                     *for and either sends it to another client or adds a new 
                     *client in case of a init message
                     */
                    switch (((int*)buffer)[0]) {
                        //Init message, the initializing message
                    case 0: {
                        cout << "Case 0" << endl;
                        init_message* init_ptr = (init_message*) &buffer;
                        //Add in one of the client structs
                        init_struct(new_socket, inet_ntoa(address.sin_addr), 
                                    ntohs(address.sin_port), init_ptr, 
                                    drone, img_pro, main_prog);
                    }
                        break;
                        //Coordinate message
                    case 1: {
                        cout << "Case 1" << endl;
                        coord_message* coord_msg_ = (coord_message*) 
                            &buffer;
                        msg->coord_msg = *coord_msg_;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog, 
                                     sizeof(*msg), coord_msg_->receiver);
                    }
                        break;
                        //Start message
                    case 2: {
                        cout << "Case 2" << endl;
                        start_message* start_msg_ = (start_message*) 
                            &buffer;
                        msg->start_msg = *start_msg_;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog, 
                                     sizeof(*msg), start_msg_->receiver);
                    }
                        break;
                        //Abort message
                    case 3: {
                        cout << "Case 3" << endl;
                        abort_message* abort_msg_ = (abort_message*)
                            &buffer;
                        msg->abort_msg = *abort_msg_;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog, 
                                     sizeof(*msg), abort_msg_->receiver);
                    }
                        break;
                        //Status message
                    case 4: {
                        cout << "Case 4" << endl;
                        status_message* status_msg_ = (status_message*)
                            &buffer;
                        msg->status_msg = *status_msg_;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog, 
                                     sizeof(*msg), status_msg_->receiver);
                    }					
                        break;
                    case 5: {
                        cout << "Case 5" << endl;
                        coords_ok_message* coords_ok = (coords_ok_message*)
                            &buffer;
                        msg->coords_ok = *coords_ok;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog,
                                     sizeof(*msg), coords_ok->receiver);
                    }
                        break;
                    case 6: {
                        cout << "Case 6" << endl;
                        drone_at_waypoint* drone_wp = (drone_at_waypoint*)
                            &buffer;
                        msg->drone_wp = *drone_wp;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog,
                                     sizeof(*msg), drone_wp->receiver);
                    }
                        break;
                    case 7: {
                        cout << "Case 7" << endl;
                        image_message* image_msg = (image_message*)&buffer;
                        msg->image_msg = *image_msg;
                        //Send it to receiving client
                        send_message(msg, drone, img_pro, main_prog, sizeof(*msg), image_msg->receiver);
                    }
                        break;
                    default: {
                        cout << "Message type not recognized" << endl;
                    }
                    };

                    //Which clients are currently connected to the server
                    cout << "The clients are: drone " << drone->init_bool << 
                        ", img " << img_pro->init_bool << ", main " <<  
                        main_prog->init_bool << endl;
                }   
            }
        }   
    }   
    return 0;   

}

/*
 *Sets up the structs for the given client
 */
void init_struct(int socket, char* ip, int port, init_message* msg_ptr, 
                 struct client* drone, struct client* img_pro, 
                 struct client* main_prog) {
    //If it's the drone
    if (msg_ptr->sender == 'D') {
        drone->init_bool = true;
        drone->sock_fd = socket;
        drone->ip_address = ip;
        drone->port = port;
        cout <<	"Init drone done!" << endl;
    }
  
    //If it's the image processing
    if (msg_ptr->sender == 'I') {
        img_pro->init_bool = true;
        img_pro->sock_fd = socket;
        img_pro->ip_address = ip;
        img_pro->port = port;
        cout << "Init Img done!" << endl;
    }
  
    //If it's the main program
    if (msg_ptr->sender == 'M') {
        main_prog->init_bool = true;
        main_prog->sock_fd = socket;
        main_prog->ip_address = ip;
        main_prog->port = port;
        cout << "Init main done!" << endl;
    }
}

/*
 *Sends a uMessage (defined at the top of this file) to a specified client
 */
void send_message(uMessage* msg_ptr, struct client* drone, 
                  struct client* img_pro, struct client* main_prog, 
                  size_t size, char receiver) {
    switch(receiver) {
        //If the receiver is the drone
    case 'D':
        //Wait until the drone connected to the server (if it isn't already)
        while(!drone->init_bool){}

        cout << "Sends drone a packet" << endl;
        cout << endl << "Sends drone a packet " << drone->sock_fd << " " 
             << size << endl;
  
        //Try to send the message
        if(send(drone->sock_fd, (char*)msg_ptr, size, 0)==-1) {
            cout << endl << "Sending to drone failed!" << endl;
        }
        break;
  
        //If the receiver is the image processing
    case 'I':
        /*
         *Wait until the image processing is connected to the server (if it
         *isn't already)
         */
        while(!img_pro->init_bool){}
        cout <<"Sends img a packet" << endl;
        cout << endl << "Sends img a packet " << img_pro->sock_fd << " " 
             << size << endl;

        //Try to send the message
        if (send(img_pro->sock_fd, (char*) msg_ptr, size, 0) == -1) {
            cout << endl << "Sending to image processing failed!" << endl;
        }
        break;
  
        //If the receiver is the main program
    case 'M':
        /*
         *Wait until the main program is connected to the server (if it 
         *isn't already)
         */
        while(!main_prog->init_bool){}
        cout << endl << "Sends main prog a packet " << main_prog->sock_fd 
             << " " << size << endl;

        //Try to send the message
        if (send(main_prog->sock_fd, (char*) msg_ptr, size, 0) == -1) {
            cout << endl << "Sending to main program failed!" << endl;
        }
        break;
    }
}

/*
* Returns -1 if an error occured w the stream, -2 if the socket closed,
* 1 if successful run.
*/
int send_image(int socket){

    //Open stream
    fstream fs;

    //Error handling
    bool open_fs = true;
    while (open_fs)
    {
        //Open up stream for writing
        fs.open("pig.jpg", std::fstream::in | std::fstream::binary);

        //If file can not be opened, ask user to try again
        if(!fs.is_open()) {
            cout << "Error has occurred. Image file could not be opened, would you like to try again? (Y/n)" << endl;
            char ans;
            cin >> ans;
            if (ans == 'n')
            {
                open_fs = false;
                return -1;
            }
        }
        else open_fs = false;
    }

    //Declare variables for size, status of buffer and packet index
    int size, stat, packet_index = 1;

    //Find size of imagefile with iterator
    cout << "Getting Picture Size" << endl;
    fs.seekg(0, fs.end);
    size = fs.tellg();
    fs.seekg(0, fs.beg);
    cout << "Total Picture size: " << size << endl;

    //Declare buffers for sending and reading data
    char send_buffer[10240], read_buffer[256];
    //Kankse ändra till dynamiskt allokerat minne.
    //Alt. fråga om bildstorlek från drönare innan körning
    //char* send_buffer = new char[size];

    //Send Picture Size through socket
    cout << "Sending Picture Size" << endl;
    write(socket, (void*)&size, sizeof(size));

    //Read from socket while checking for errors that are due to signals.
    do {
        stat = read(socket, &read_buffer , sizeof(read_buffer));
        cout << "Bytes read: " << stat << endl;
    } while (stat < 0);
    //Check if status of socket is bad, terminate function
    if(stat == 0){
        cout << "Socket is closed! Can't receive message." << endl;
        return -2;
    }

    cout << "Received data in socket\n" << endl;
    cout << "Socket data: " << read_buffer << endl << endl;

    //Send Picture as Byte Array through socket
    cout << "Sending Picture as Byte Array" << endl;

    //While the stream is not empty, send a part of the image
    //through the socket. Image part is sent in a package with size of send buffer
    while(!fs.eof()) {
       //Read from the file into our send buffer until send buffer is full
        fs.read(send_buffer, sizeof(send_buffer));

       //Send data through socket
        do{
            stat = write(socket, send_buffer, fs.gcount());
        } while (stat < 0);

        //Check if status of socket is bad, terminate function
        if(stat == 0){
            cout << "Socket is closed! Can't send image." << endl;
            return -2;
        }

       //Print out package number and package size
        cout << "Packet Number: " << packet_index << endl;
        cout << "Packet Size Sent: " << fs.gcount() << endl << endl;

       //Increment package index
        packet_index++;

       //Zero out our send buffer
        bzero(send_buffer, sizeof(send_buffer));
    }

    return 1;
}
