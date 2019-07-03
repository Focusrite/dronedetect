#ifndef MESSAGE_H
#define MESSAGE_H

struct message {
    int type;
    char sender;
    char receiver;
};

struct init_message {
    int type;
    char sender;
    char receiver;

};

struct coord_message {
//private:
    int type;
//public:
    char sender;
    char receiver;

    double lon;
    double lat;
    double alt;

    //int get_type() {
      //  return type;
    //}
};

struct start_message {
//private:
    int type;
//public:
    char sender;
    char receiver;

    //int get_type() {
    //    return type;
    //}
};

struct abort_message {
//private:
    int type;
//public:
    char sender;
    char receiver;

    //int get_type() {
    //    return type;
    //}
};

struct status_message {
//private:
    int type;
//public:
    char sender;
    char receiver;

    double lon;
    double lat;
    double alt;

    int battery_status;

    /*int get_type() {
        return type;
    }*/
};

struct coords_ok_message {
//private:
    int type;
//public:
    char sender;
    char receiver;
    int ok;

    /*int get_type() {
        return type;
    }*/
};

struct drone_at_waypoint {
    int type;
    char sender;
    char receiver;

};

struct image_message {
    int type;
    char sender;
    char receiver;
    int image_size;
};

#endif // MESSAGE_H
