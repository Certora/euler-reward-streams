// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.0;

import {Set, SetStorage} from "evc/Set.sol";


/// @title Exposes the internal function of the Set library
contract SetHarness {

    SetStorage public setStorage;

    function insert(
        address element
    ) external returns (bool wasInserted) {
        return Set.insert(setStorage, element);
    }

    function remove(
        address element
    ) external returns (bool) {
        return Set.remove(setStorage, element);
    }

    /// @notice Returns the element at index - 1
    function get(uint8 index) external view returns (address) {
        if (index == 0) return address(0);
        if (index == 1) return setStorage.firstElement;
        return setStorage.elements[index - 1].value;
    }

    function contains(
        address element
    ) external view returns (bool found) {
        return Set.contains(setStorage, element);
    }

    function length(
    ) external view returns (uint8) {
        return setStorage.numElements;
    }
}
