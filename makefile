# Config
PROTO_ZIP ?= proto-files.zip
PROTO_DIR := proto
MODELS_DIR := fennel_invest_api/models

# Targets
.PHONY: all setup generate clean

all: fix

# Create necessary folders and unzip the .proto archive
setup:
	@echo "Setting up directories..."
	mkdir -p $(PROTO_DIR)
	mkdir -p $(MODELS_DIR)
	@if [ -f "$(PROTO_ZIP)" ]; then \
		echo "Unzipping $(PROTO_ZIP) into $(PROTO_DIR)..."; \
		unzip -o $(PROTO_ZIP) -d $(PROTO_DIR); \
	else \
		echo "No $(PROTO_ZIP) found, please run from the root project directory."; \
	fi

# Generate protobuf Python stubs
generate: setup
	@echo "Generating protobuf Python files..."
	protoc \
		-I=$(PROTO_DIR) \
		--python_out=$(MODELS_DIR) \
		--pyi_out=$(MODELS_DIR) \
		$(PROTO_DIR)/*.proto
	@echo "Generation complete. Files written to $(MODELS_DIR)."

# Fix relative imports in generated protobuf files
fix: generate
	@echo "Fixing protobuf imports..."
	fix-protobuf-imports $(MODELS_DIR)
	@echo "Import fix complete."

# Clean generated code
clean:
	@echo "Cleaning generated protobuf files..."
	find $(MODELS_DIR) -type f \( -name '*_pb2.py' -o -name '*_pb2.pyi' \) -delete
	rm -rf $(PROTO_DIR)
	@echo "Clean complete."
