# FTP-Q Protocol – Part 3

**Student**: Ishan Patel  
**ID**: 14681007  
**Course**: CS 544 – Computer Networks  
**Assignment**: Part 3 – Protocol Implementation

## Overview

This project implements a TCP-based file transfer protocol (FTP-Q) with the following features:

## Features

- Custom message types: `FileMeta`, `FileChunk`, `FileAck`
- Chunked file transfer with byte-offsets
- 3-state DFA: `INIT → TRANSFER → DONE`
- Server-side file reassembly
- SHA-256 integrity check
- Resume from offset using `FileAck`
- Protocol version negotiation

## How to Run

1. **Start the server:**
   ```bash
   python3 -m server.server
   ```
2. **Start the client:**
   ```bash
   python3 -m client.server
   ```
