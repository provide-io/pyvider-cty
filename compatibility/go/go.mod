// This file defines the Go module for our compatibility test fixture generator.
// It explicitly lists the required dependencies.

module github.com/pyvider/cty-compat-generator

go 1.21

require (
	github.com/hashicorp/go-hclog v1.6.3
	github.com/spf13/cobra v1.8.1
	github.com/zclconf/go-cty v1.14.4
)

require (
	github.com/apparentlymart/go-textseg/v15 v15.0.0 // indirect
	github.com/fatih/color v1.13.0 // indirect
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/mattn/go-colorable v0.1.12 // indirect
	github.com/mattn/go-isatty v0.0.14 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	github.com/vmihailenco/msgpack/v5 v5.3.5 // indirect
	github.com/vmihailenco/tagparser/v2 v2.0.0 // indirect
	golang.org/x/sys v0.5.0 // indirect
	golang.org/x/text v0.11.0 // indirect
)

// Indirect dependencies will be managed by 'go mod tidy'
