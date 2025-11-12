# FlexRIC Energy Saving xApp Makefile
# Targets 37% energy reduction through TX chain management

CC = gcc
CFLAGS = -Wall -Wextra -std=gnu11 -fPIC -g -O2
LDFLAGS = -shared -fPIC

# FlexRIC paths (adjust according to your installation)
FLEXRIC_ROOT = /home/erena/flexric
FLEXRIC_BUILD = $(FLEXRIC_ROOT)/build
FLEXRIC_SRC = $(FLEXRIC_ROOT)/src

# Include directories
INCLUDES = -I$(FLEXRIC_SRC) \
           -I$(FLEXRIC_SRC)/xApp \
           -I$(FLEXRIC_SRC)/sm/mac_sm \
           -I$(FLEXRIC_SRC)/sm/mac_sm/ie \
           -I$(FLEXRIC_SRC)/util \
           -I$(FLEXRIC_SRC)/lib \
           -I/usr/include/e2ap \
           -I/usr/local/include

# Library directories and libraries
LIBDIRS = -L$(FLEXRIC_BUILD)/src/lib \
          -L$(FLEXRIC_BUILD)/src/xApp \
          -L$(FLEXRIC_BUILD)/src/sm/mac_sm \
          -L/usr/local/lib \
          -L/usr/lib/x86_64-linux-gnu

LIBS = -le42_xapp_api \
       -lmac_sm \
       -lsctp \
       -lpthread \
       -lm \
       -lrt

# Source files
SOURCES = xapp_energy_save.c
HEADERS = xapp_energy_save.h
TARGET = xapp_energy_save
SHARED_LIB = libxapp_energy_save.so

# Default target
all: $(TARGET) $(SHARED_LIB)

# Compile the executable
$(TARGET): $(SOURCES) $(HEADERS)
	@echo "=== Building FlexRIC Energy Saving xApp ==="
	@echo "Target: 37% energy reduction through deep-sleep"
	@echo "Trigger: No PDSCH for 500ms + No HARQ failures"
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $(SOURCES) $(LIBDIRS) $(LIBS)
	@echo "✓ xApp executable built: $(TARGET)"

# Compile the shared library
$(SHARED_LIB): $(SOURCES) $(HEADERS)
	@echo "=== Building shared library ==="
	$(CC) $(CFLAGS) $(LDFLAGS) $(INCLUDES) -o $@ $(SOURCES) $(LIBDIRS) $(LIBS)
	@echo "✓ Shared library built: $(SHARED_LIB)"

# Install target
install: $(TARGET) $(SHARED_LIB)
	@echo "=== Installing Energy Saving xApp ==="
	sudo mkdir -p /home/erena/flexric/build/examples/c/xApp/energy_save
	sudo cp $(TARGET) /home/erena/flexric/build/examples/c/xApp/energy_save
	sudo cp $(SHARED_LIB) /home/erena/flexric/build/examples/c/xApp/energy_save
	sudo cp $(HEADERS) /home/erena/flexric/build/examples/c/xApp/energy_save
	@echo "✓ Installation complete"

# Test compilation without linking
test-compile: $(SOURCES) $(HEADERS)
	@echo "=== Testing compilation ==="
	$(CC) $(CFLAGS) $(INCLUDES) -c $(SOURCES) -o xapp_energy_save.o
	@echo "✓ Compilation test passed"

# Clean build artifacts
clean:
	@echo "=== Cleaning build artifacts ==="
	rm -f $(TARGET) $(SHARED_LIB) *.o *.so
	@echo "✓ Clean complete"

# Debug build
debug: CFLAGS += -DDEBUG -g3
debug: $(TARGET)
	@echo "✓ Debug build complete"

# Check FlexRIC dependencies
check-deps:
	@echo "=== Checking FlexRIC Dependencies ==="
	@echo "FlexRIC Root: $(FLEXRIC_ROOT)"
	@if [ -d "$(FLEXRIC_ROOT)" ]; then \
		echo "✓ FlexRIC directory found"; \
	else \
		echo "✗ FlexRIC directory not found at $(FLEXRIC_ROOT)"; \
		echo "  Please adjust FLEXRIC_ROOT in Makefile"; \
	fi
	@if [ -d "$(FLEXRIC_BUILD)" ]; then \
		echo "✓ FlexRIC build directory found"; \
	else \
		echo "✗ FlexRIC build directory not found"; \
		echo "  Please build FlexRIC first"; \
	fi
	@if [ -f "$(FLEXRIC_BUILD)/src/lib/libe42_xapp_api.so" ]; then \
		echo "✓ FlexRIC xApp API library found"; \
	else \
		echo "✗ FlexRIC xApp API library not found"; \
	fi
	@echo "=== Dependency Check Complete ==="

# Print build configuration
config:
	@echo "=== Build Configuration ==="
	@echo "Compiler: $(CC)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo "Includes: $(INCLUDES)"
	@echo "Libraries: $(LIBS)"
	@echo "Target: $(TARGET)"
	@echo "=========================="

# Quick test run (requires FlexRIC RIC running)
test-run: $(TARGET)
	@echo "=== Testing Energy Saving xApp ==="
	@echo "NOTE: Ensure FlexRIC RIC is running at oai-ric.green-xg.svc.cluster.local:36421"
	@echo "Press Ctrl+C to stop"
	./$(TARGET)

.PHONY: all clean install debug check-deps config test-compile test-run

# Help target
help:
	@echo "FlexRIC Energy Saving xApp Build System"
	@echo "======================================="
	@echo ""
	@echo "Available targets:"
	@echo "  all         - Build both executable and shared library"
	@echo "  clean       - Remove build artifacts"
	@echo "  install     - Install xApp to FlexRIC directory"
	@echo "  debug       - Build with debug symbols"
	@echo "  test-compile- Test compilation without linking"
	@echo "  check-deps  - Check FlexRIC dependencies"
	@echo "  config      - Show build configuration"
	@echo "  test-run    - Build and run xApp (requires RIC)"
	@echo "  help        - Show this help"
	@echo ""
	@echo "Energy Saving Features:"
	@echo "  • Monitors PDSCH scheduling activity"
	@echo "  • Triggers deep-sleep after 500ms of inactivity"
	@echo "  • Achieves 37% energy reduction"
	@echo "  • Zero HARQ failure tolerance"
	@echo "  • Automatic TX chain management"