//
//  File.swift
//  projeto_redes
//
//  Created by João Vitor Rocha Miranda on 26/09/25.
//

import Fluent
import Vapor

struct MessageDTO: Content{
    var id: UUID?
    var client_ip: String?
    var message: String?
    
}
