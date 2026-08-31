"""CPU Workflow Module - Packet Layer

Binary packet assembly, parsing, and transmission.
"""

from typing import Any, Dict, Optional, List
from core.base import BaseComponent
from core.exceptions import PacketError
import struct
import json
from datetime import datetime


class Packet(BaseComponent):
    """Packet component for binary data handling."""

    def __init__(self, packet_id: str = 'packet_01', config: Optional[Dict[str, Any]] = None):
        """Initialize Packet component.
        
        Args:
            packet_id: Unique identifier for the packet manager
            config: Optional configuration dictionary
        """
        super().__init__(packet_id, 'Packet', config)
        self.packets = {}
        self.assembly_buffer = bytearray()

    def create_packet(self, packet_type: str, data: Any, sequence: int = 0) -> bytes:
        """Create a binary packet.
        
        Args:
            packet_type: Type of packet
            data: Packet payload
            sequence: Sequence number
            
        Returns:
            Binary packet
        """
        try:
            # Packet header: type (2 bytes) + sequence (4 bytes) + length (4 bytes)
            payload = json.dumps(data).encode('utf-8')
            header = struct.pack('!HI', self._type_to_int(packet_type), sequence)
            length = struct.pack('!I', len(payload))
            packet = header + length + payload
            return packet
        except Exception as e:
            raise PacketError(f"Packet creation failed: {e}")

    def parse_packet(self, packet: bytes) -> Dict[str, Any]:
        """Parse a binary packet.
        
        Args:
            packet: Binary packet data
            
        Returns:
            Parsed packet information
        """
        try:
            if len(packet) < 10:
                raise PacketError("Packet too small")
            
            packet_type, sequence = struct.unpack('!HI', packet[:6])
            length = struct.unpack('!I', packet[6:10])[0]
            payload = packet[10:10+length].decode('utf-8')
            
            return {
                'type': self._int_to_type(packet_type),
                'sequence': sequence,
                'length': length,
                'payload': json.loads(payload)
            }
        except Exception as e:
            raise PacketError(f"Packet parsing failed: {e}")

    def assemble_packets(self, packets: List[bytes]) -> bytes:
        """Assemble multiple packets.
        
        Args:
            packets: List of binary packets
            
        Returns:
            Assembled data
        """
        assembled = bytearray()
        for packet in packets:
            parsed = self.parse_packet(packet)
            assembled.extend(parsed['payload'].encode('utf-8'))
        return bytes(assembled)

    def fragment_data(self, data: bytes, chunk_size: int = 1024) -> List[bytes]:
        """Fragment data into packets.
        
        Args:
            data: Data to fragment
            chunk_size: Size of each chunk
            
        Returns:
            List of packet fragments
        """
        fragments = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            packet = self.create_packet('DATA', chunk.decode('utf-8', errors='ignore'), sequence=i//chunk_size)
            fragments.append(packet)
        return fragments

    def _type_to_int(self, packet_type: str) -> int:
        """Convert packet type to integer.
        
        Args:
            packet_type: Packet type string
            
        Returns:
            Integer representation
        """
        types = {'DATA': 1, 'CONTROL': 2, 'ACK': 3, 'ERROR': 4}
        return types.get(packet_type, 0)

    def _int_to_type(self, packet_int: int) -> str:
        """Convert integer to packet type.
        
        Args:
            packet_int: Integer representation
            
        Returns:
            Packet type string
        """
        types = {1: 'DATA', 2: 'CONTROL', 3: 'ACK', 4: 'ERROR'}
        return types.get(packet_int, 'UNKNOWN')

    def process(self, data: Any) -> Any:
        """Process data through packet layer.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        if not self.is_active:
            return data
        return data
