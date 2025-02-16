
CXX = g++
CXXFLAGS = -I/usr/local/lib/ILI9341/include
LDFLAGS = -L/usr/local/lib/ILI9341/lib -lrpidisplaygl -llgpio

SRC = src/screen.cpp
OUT = screen

all: $(OUT)

$(OUT): $(SRC)
	$(CXX) $(SRC) -o $(OUT) $(CXXFLAGS) $(LDFLAGS)

clean:
	rm -f $(OUT)
	rm -f obj/*

run: $(OUT)
	./$(OUT)

install: $(OUT)
	# Add any install commands here if needed, e.g., copy to a bin directory
	# sudo cp $(OUT) /usr/local/bin/

.PHONY: all clean run install

