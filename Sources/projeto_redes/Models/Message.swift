//
//  File.swift
//  projeto_redes
//
//  Created by João Vitor Rocha Miranda on 26/09/25.
//

import Fluent
import Vapor
import Foundation

final class Message: Model, @unchecked Sendable{
    
    static let schema = "TB_Messages"
    
    @ID(key: .id)
    var id: UUID?
    
    @Field(key: "client_ip")
    var client_ip: String
    
    @Field(key: "message")
    var message: String
    
    init() {}
    init(id: UUID? = nil, client_ip: String, message: String) {
        self.id = id
        self.client_ip = client_ip
        self.message = message
    }
    
    func toDTO() -> MessageDTO{
        .init(
            id: self.id,
            client_ip: self.$client_ip.value,
            message: self.$message.value
        )
    }
}
