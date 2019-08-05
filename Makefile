# Makefile for Detector program
.PHONY: all clean

# Installation directories for pylon
PYLON_ROOT := /home/user/sommarjobb/pylon/pylon5

# Build tools and flags
LD         := $(CXX)
CPPFLAGS   := $(shell $(PYLON_ROOT)/bin/pylon-config --cflags)
CXXFLAGS   := -std=c++11 #e.g., CXXFLAGS=-g -O0 for debugging
LDFLAGS    := $(shell $(PYLON_ROOT)/bin/pylon-config --libs-rpath)
LDLIBS     := $(shell $(PYLON_ROOT)/bin/pylon-config --libs)
OPENCV     := `pkg-config --libs opencv`

# Rules for building
all: detector

detector: Detector.o cap.o Triangulator.o
	$(LD) $(LDFLAGS) -o $@ $^ $(LDLIBS) $(OPENCV)

Detector.o: Detector.cc Detector.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

cap.o: cap.cc cap.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

Triangulator.o: Triangulator.cc Triangulator.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

clean:
	$(RM) $(NAME).o $(NAME)
